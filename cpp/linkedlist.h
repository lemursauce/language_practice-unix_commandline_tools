#ifndef LINKED_LIST_H
#define LINKED_LIST_H

#include <sys/types.h>

template <typename T>
struct Node {
    T data;
    Node* prev;
    Node* next;

    Node() = default;
    Node(T data) : data(data) {}
    Node(T data, Node* prev, Node* next) : data(data) , prev(prev), next(next) {}
    ~Node() {}
};

template <typename T>
class List {
private:
    Node<T> head;
    Node<T> tail;
    size_t _size = 0;

    class Iterator {
    private:
        Node<T>* node;
    public:
        Iterator(Node<T> * node) : node(node) {}

        T& operator*() {
            return node->data;
        }
        T* operator->() {
            return &(node->data);    
        }

        Iterator& operator++() {
            node = node->next;
            return *this;
        }
        Iterator operator++(int) {
            Iterator temp = *this;
            ++(*this);
            return temp;
        }

        Iterator& operator--() {
            node = node->prev;
            return *this;
        }
        Iterator operator--(int) {
            Iterator temp = *this;
            --(*this);
            return temp;
        }

        bool operator==(const Iterator& other) {
            return node == other.node;
        }
        bool operator!=(const Iterator& other) {
            return node != other.node;
        }
    };

public:
    List() {
        _size = 0;

        head.prev = nullptr;
        head.next = &tail;
        tail.prev = &head;
        tail.next = nullptr;
    }
    ~List() {
        Node<T> * it = head.next;
        Node<T> * temp;
        while (it != &tail) {
            temp = it->next;
            delete it;
            it = temp;
        }
    }

    void push_front(T val) {
        Node<T> * temp = new Node<T>(val, &head, head.next);
        head.next->prev = temp;
        head.next = temp;
        ++_size;
    }
    void push_back(T val) {
        Node<T> * temp = new Node<T>(val, tail.prev, &tail);
        tail.prev->next = temp;
        tail.prev = temp;
        ++_size;
    }

    bool pop_front() {
        if (head.next == &tail) return false;
        head.next = head.next->next;
        delete head.next->prev;
        head.next->prev = &head;
        --_size;
        return true;
    }
    bool pop_back() {
        if (tail.prev == &head) return false;
        tail.prev = tail.prev->prev;
        delete tail.prev->next;
        tail.prev->next = &tail;
        --_size;
        return true;
    }

    T front() {
        return head.next->data;
    }
    T back() {
        return tail.prev->data;
    }

    Iterator begin() {
        return Iterator(head.next);
    }
    Iterator end() {
        return Iterator(&tail);
    }

    size_t size() {
        return _size;
    }

    bool empty() {
        return (_size == 0);
    }

    void clear() {
        Node<T> * it = head.next;
        while (it != &tail) {
            it = it->next;
            delete head.next;
            head.next = it;
        }
        tail.prev = &head;
        _size = 0;
    }
};

#endif